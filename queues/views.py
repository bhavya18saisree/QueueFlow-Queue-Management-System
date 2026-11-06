
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from .models import Queue, Token


# Keep waiting-list positions in correct order
def normalize_waiting_positions(queue):
    waiting_tokens = Token.objects.filter(
        queue=queue,
        status='Waiting'
    ).order_by('position', 'id')

    for position, waiting_token in enumerate(waiting_tokens, start=1):
        waiting_token.position = position

    Token.objects.bulk_update(
        waiting_tokens,
        ['position']
    )



# Dashboard
@login_required
def dashboard(request):

    queues = Queue.objects.filter(manager=request.user)

    total_queues = queues.count()

    waiting_tokens = Token.objects.filter(
        queue__manager=request.user,
        status='Waiting'
    ).count()

    serving_tokens = Token.objects.filter(
        queue__manager=request.user,
        status='Serving'
    ).count()

    completed_tokens = Token.objects.filter(
        queue__manager=request.user,
        status='Served'
    ).count()

    cancelled_tokens = Token.objects.filter(
        queue__manager=request.user,
        status='Cancelled'
    ).count()

    # Calculate average waiting time
    served_tokens = Token.objects.filter(
        queue__manager=request.user,
        status='Served',
        called_at__isnull=False
    )

    waiting_times = []

    for token in served_tokens:
        waiting_time = token.called_at - token.created_at
        waiting_times.append(
            waiting_time.total_seconds() / 60
        )

    average_waiting_time = (
        round(sum(waiting_times) / len(waiting_times), 2)
        if waiting_times else 0
    )

    # Calculate average service time
    service_times = []

    for token in served_tokens.filter(completed_at__isnull=False):
        service_time = token.completed_at - token.called_at
        service_times.append(
            service_time.total_seconds() / 60
        )

    average_service_time = (
        round(sum(service_times) / len(service_times), 2)
        if service_times else 0
    )

    # Get current waiting count for each queue
    queue_lengths = []
    queue_chart_labels = []
    queue_chart_values = []

    for queue in queues:
        waiting_count = Token.objects.filter(
            queue=queue,
            status='Waiting'
        ).count()

        queue_lengths.append({
            'name': queue.name,
            'waiting_count': waiting_count,
        })

        queue_chart_labels.append(queue.name)
        queue_chart_values.append(waiting_count)

    # Token status chart data
    token_status_chart = {
        'labels': [
            'Waiting',
            'Serving',
            'Served',
            'Cancelled',
        ],
        'values': [
            waiting_tokens,
            serving_tokens,
            completed_tokens,
            cancelled_tokens,
        ],
    }

    # Queue load chart data
    queue_load_chart = {
        'labels': queue_chart_labels,
        'values': queue_chart_values,
    }

    # Send dashboard data to HTML template
    context = {
        'total_queues': total_queues,
        'waiting_tokens': waiting_tokens,
        'serving_tokens': serving_tokens,
        'completed_tokens': completed_tokens,
        'cancelled_tokens': cancelled_tokens,
        'average_waiting_time': average_waiting_time,
        'average_service_time': average_service_time,
        'queue_lengths': queue_lengths,
        'token_status_chart': token_status_chart,
        'queue_load_chart': queue_load_chart,
    }

    return render(request, 'dashboard.html', context)

# Manage Queues
@login_required
def manage_queues(request):

    if request.method == 'POST':
        queue_name = request.POST.get('queue_name', '').strip()

        if queue_name:
            Queue.objects.create(
                name=queue_name,
                manager=request.user
            )

        return redirect('manage_queues')

    queues = Queue.objects.filter(
        manager=request.user
    ).order_by('-created_at')

    return render(
        request,
        'queues.html',
        {'queues': queues}
    )


# Queue Details and Add Customer
@login_required
def queue_details(request, queue_id):

    queue = get_object_or_404(
        Queue,
        id=queue_id,
        manager=request.user
    )

    if request.method == 'POST':

        person_name = request.POST.get(
            'person_name', ''
        ).strip()

        if person_name:

            with transaction.atomic():

                # Lock queue while generating token
                Queue.objects.select_for_update().get(
                    id=queue.id
                )

                # Get waiting tokens in existing order
                waiting_tokens = list(
                    Token.objects.select_for_update()
                    .filter(
                        queue=queue,
                        status='Waiting'
                    )
                    .order_by('position', 'id')
                )

                # Correct waiting positions
                for position, waiting_token in enumerate(
                    waiting_tokens, start=1
                ):
                    waiting_token.position = position

                if waiting_tokens:
                    Token.objects.bulk_update(
                        waiting_tokens,
                        ['position']
                    )

                # Generate next token number
                last_token = Token.objects.filter(
                    queue=queue
                ).order_by('-token_number').first()

                next_token_number = (
                    last_token.token_number + 1
                    if last_token else 1
                )

                # Add customer at end of waiting list
                Token.objects.create(
                    queue=queue,
                    person_name=person_name,
                    token_number=next_token_number,
                    position=len(waiting_tokens) + 1
                )

        return redirect(
            'queue_details',
            queue_id=queue.id
        )

    # Display waiting tokens first
    waiting_tokens = list(
        Token.objects.filter(
            queue=queue,
            status='Waiting'
        ).order_by('position', 'id')
    )

    # Display other tokens as history
    other_tokens = list(
        Token.objects.filter(queue=queue)
        .exclude(status='Waiting')
        .order_by('-created_at', '-id')
    )

    tokens = waiting_tokens + other_tokens

    return render(
        request,
        'queue_details.html',
        {
            'queue': queue,
            'tokens': tokens
        }
    )


# Move Token Up or Down
@login_required
def move_token(request, token_id, direction):

    token = get_object_or_404(
        Token,
        id=token_id,
        queue__manager=request.user
    )

    if request.method == 'POST':

        with transaction.atomic():

            # Get only active waiting tokens
            waiting_tokens = list(
                Token.objects.select_for_update()
                .filter(
                    queue=token.queue,
                    status='Waiting'
                )
                .order_by('position', 'id')
            )

            # Find selected token
            current_index = next(
                (
                    index
                    for index, item in enumerate(waiting_tokens)
                    if item.id == token.id
                ),
                None
            )

            if current_index is not None:

                target_index = current_index

                if direction == 'up' and current_index > 0:
                    target_index = current_index - 1

                elif (
                    direction == 'down'
                    and current_index < len(waiting_tokens) - 1
                ):
                    target_index = current_index + 1

                # Swap selected token with neighbour
                if target_index != current_index:
                    waiting_tokens[current_index], waiting_tokens[target_index] = (
                        waiting_tokens[target_index],
                        waiting_tokens[current_index]
                    )

                # Reassign sequential positions
                for position, waiting_token in enumerate(
                    waiting_tokens, start=1
                ):
                    waiting_token.position = position

                Token.objects.bulk_update(
                    waiting_tokens,
                    ['position']
                )

    return redirect(
        'queue_details',
        queue_id=token.queue.id
    )


# Mark Token as Served
@login_required
def complete_token(request, token_id):

    token = get_object_or_404(
        Token,
        id=token_id,
        queue__manager=request.user
    )

    if request.method == 'POST' and token.status == 'Serving':

        with transaction.atomic():

            token.status = 'Served'
            token.completed_at = timezone.now()

            token.save(
                update_fields=['status', 'completed_at']
            )

            # Correct remaining waiting positions
            normalize_waiting_positions(token.queue)

    return redirect(
        'queue_details',
        queue_id=token.queue.id
    )


# Cancel Token
@login_required
def cancel_token(request, token_id):

    token = get_object_or_404(
        Token,
        id=token_id,
        queue__manager=request.user
    )

    if request.method == 'POST' and token.status == 'Waiting':

        with transaction.atomic():

            token.status = 'Cancelled'
            token.save(
                update_fields=['status']
            )

            # Correct remaining waiting positions
            normalize_waiting_positions(token.queue)

    return redirect(
        'queue_details',
        queue_id=token.queue.id
    )


# Call Next Waiting Token
@login_required
def call_next_token(request, queue_id):

    queue = get_object_or_404(
        Queue,
        id=queue_id,
        manager=request.user
    )

    if request.method == 'POST':

        with transaction.atomic():

            # Check whether someone is already being served
            current_serving = Token.objects.filter(
                queue=queue,
                status='Serving'
            ).first()

            if not current_serving:

                # Get the first waiting customer
                next_token = Token.objects.filter(
                    queue=queue,
                    status='Waiting'
                ).order_by('position', 'id').first()

                if next_token:

                    next_token.status = 'Serving'
                    next_token.called_at = timezone.now()

                    next_token.save(
                        update_fields=['status', 'called_at']
                    )

                    # Update remaining waiting positions
                    normalize_waiting_positions(queue)

    return redirect(
        'queue_details',
        queue_id=queue.id
    )
