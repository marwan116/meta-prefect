# """Adds a slack notifier to the deployment."""
# from meta_prefect.interface import DeployableFlowBuilderInterface, Deployment
# from prefect.events.schemas import Automation, Notification, Posture, Trigger
# from prefect.utilities.asyncutils import sync_compatible
# from pydantic import BaseModel


# class slack_notifier(BaseModel, DeployableFlowBuilderInterface):
#     """A slack notifier."""

#     def _build_slack_message(self):
#         return """
#         Flow run {{ flow_run.name }} entered state {{ flow_run.state.name }}.

#             Timestamp: {{ flow_run.state.timestamp }}
#             Flow ID: {{ flow_run.flow_id }}
#             Flow Run ID: {{ flow_run.id }}
#             State message: {{ flow_run.state.message }}
#         """

#     @sync_compatible
#     async def update_deployment(
#        self, flow: DeployableFlow, deployment: Deployment
#    ) -> Deployment:
#         deployment.notifications = [
#             {
#                 "type": "slack",
#                 "flow_run_states": ["Running", "Success", "Failed"],
#                 "template": self._build_slack_message(),
#                 "channels": ["#meta-prefect"],
#             }
#         ]
#         return Automation(
#             name="Slack automation on flow run state change",
#             description=f"""
#                 This automation will send a slack message to {channel=}
#                 when a flow run enters a new state.
#             """,
#             enabled=True,
#             trigger=Trigger(
#                 posture=Posture.Reactive,
#                 threshold=1,
#                 within=datetime.timedelta(0),
#             ),
#             actions=[],
#             owner_resource=f"prefect.deployment.{deployment.id}",
#         )
