---
name: send
track: bonus
kind: action
provider: Telegram Bot API
requires_env: [TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]
inputs: [text, confirmed]
outputs: [status]
side_effect: true
requires_confirmation: true
---
# send

Posts text to a Telegram channel. The message is only sent when `confirmed` is the boolean `True`; truthy strings or numbers do not count as confirmation.

Only post to the configured private group channel after approval of the exact text in the current conversation. A preparation request is not publication approval.
