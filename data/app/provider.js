// app/provider.js
window.ProviderDataService = {
  GRAPHQL_URL: "http://127.0.0.1:7600/graphql",

  // Fetch provider configurations via GraphQL and structure it for the UI table
  async fetchProviders() {
    const query = `
      query {
        provider {
          name
          function
          active
          domain
          api
          kms
          terms
          description
        }
      }
    `;

    const headers = [
      "name",
      "function",
      "active",
      "domain",
      "api",
      "kms",
      "terms",
      "description",
    ];

    try {
      const response = await fetch(this.GRAPHQL_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok)
        throw new Error(`HTTP-Error! Status: ${response.status}`);

      const result = await response.json();

      if (result.errors) {
        throw new Error(result.errors[0].message);
      }

      const providers = result.data?.provider || [];

      // Map the array of objects into rows of simple arrays for the table
      const rows = providers.map((item) => [
        item.name || "",
        item.function || "",
        String(item.active ?? ""),
        item.domain || "",
        item.api || "",
        item.kms || "",
        item.terms || "",
        item.description || "",
      ]);

      return { headers, rows };
    } catch (err) {
      console.warn(
        "GraphQL Fetch for providers failed. Using fallback structures:",
        err,
      );
      return {
        headers,
        rows: [],
      };
    }
  },

  // Placeholder payload structure for your update mutation when ready
  async saveProviders(serializedData) {
    console.log("Save triggered for providers:", serializedData);
    alert(
      "Provider save functionality needs a corresponding GraphQL Mutation implementation.",
    );
    return false;
  },

  serializeCSV(headers, rows) {
    return { headers, rows };
  },
};
