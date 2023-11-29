from reactpy import html, component, use_state, use_effect, run

@component
def Chatbox():
    messages, set_messages = use_state([])
    current_message, set_current_message = use_state("")

    def handle_message_change(event):
        set_current_message(event.target.value)

    async def send_message():
        if current_message:
#            response = await fetch('/send_query', {
#                'method': 'POST',
#                'headers': {
#                    'Content-Type': 'application/json',
#                },
#                'body': json.dumps({'query': current_message}),
#            })
            set_messages([messages, {'user': current_message, 'bot': response_data['answer']}]) 
            set_current_message("")

    return html.div(
        (html.div(
            html.p(message['user']),
            html.p(message['bot']),
        ) for message in messages),
        html.input(
            {"type": text,
            "value": current_message,
            "onChange":handle_message_change}
        ),
        html.button(
            {"onClick": send_message,
            "children": "Send"}
        ),
    )

run(Chatbox)