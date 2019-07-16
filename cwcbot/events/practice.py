from cwcbot.events.base_event import Event
from datetime import datetime


class Practice(Event):
    def __init__(self):
        interval_minutes = 5  # Set the interval for this event
        super().__init__(interval_minutes)

    # Override the run() method
    # It will be called once every {interval_minutes} minutes
    async def run(self, client, config):
        now = datetime.now()

        if now.weekday() == 1 or now.weekday() == 3:  # Tuesday and Thursday
            if now.hour == 15 or now.hour == 19:
                server = client.get_guild(config['server_id'])
                tw_role = server.get_role(config['tw_role_id'])
                cw_role = server.get_role(config['cw_role_id'])

                msg = f"{tw_role.mention} {cw_role.mention} "
                msg += 'EU' if now.hour == 15 else 'US'
                msg += ' Practice time!'

                channel = client.get_channel(config['practice_channel_id'])
                await channel.send(msg)
