# project/controller/aft_controller.py

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from modules.aft_builder import AFTBuilder

class AFTController:
    def __init__(self, graphql_url: str, repo_path: str, scope: str = "core"):
        self.url = graphql_url
        self.repo_path = repo_path
        self.scope = scope
        self.domain = "aft"

        transport = RequestsHTTPTransport(url=self.url, verify=True, retries=3)
        self.gql_client = Client(transport=transport, fetch_schema_from_transport=False)

    def _fetch_topology_blueprint(self) -> dict:
        query = gql("""
        query GetTopology($scope: String!) {
            account(filter: { function: $scope }) {
                name
                function
                email
            }
        }
        """)
        return self.gql_client.execute(query, variable_values={"scope": self.scope})

    def run(self):
        blueprint = self._fetch_topology_blueprint()
        accounts = blueprint.get("account", [])

        builder = AFTBuilder(self.repo_path)
        for acc in accounts:
            print(f"--> Converging AFT Account Request: {acc['name']}")
            builder.build(
                account_name=acc['name'],
                email=acc['email'],
                ou=acc['function']
            )
        return "AFT_Config_Applied"
