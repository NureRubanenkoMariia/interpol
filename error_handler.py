

class ErrorHandler:
    @staticmethod
    def handle_error(exception, message="An error occurred"):
        return {
            'success': False,
            'message': f"{message}: {str(exception)}"
        }, 500

    @staticmethod
    def handle_validation_error(message):
        if isinstance(message, dict):
            error_messages = []
            for field, errors in message.items():
                error_messages.append(f"{field}: {', '.join(errors)}")
            message = "; ".join(error_messages)

        return {
            'success': False,
            'message': message
        }, 400