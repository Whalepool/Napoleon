from functools import wraps
import utils.loadconfig as config 

#################################
# Admin control function 
# Usage: Add a @restricted decorator on top of your handler declaration:
def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        # extract user_id from arbitrary update
        try:
            user_id = update.message.from_user.id
        except (NameError, AttributeError):
            try:
                user_id = update.inline_query.from_user.id
            except (NameError, AttributeError):
                try:
                    user_id = update.chosen_inline_result.from_user.id
                except (NameError, AttributeError):
                    try:
                        user_id = update.callback_query.from_user.id
                    except (NameError, AttributeError):
                        print("No user_id available in update.")
                        return
        if user_id not in config.LIST_OF_ADMINS:
            logger.info("Unauthorized access denied for {}.".format(user_id)+" ("+update.message.from_user.username+")  message: "+update.message.text)
            return
        return func(bot, update, *args, **kwargs)
    return wrapped

