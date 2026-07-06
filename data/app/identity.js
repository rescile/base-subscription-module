// app/identity.js
window.DataService = {
  GRAPHQL_URL: "http://127.0.0.1:7600/graphql",

  // Fetch data via GraphQL and structure it for the UI table
  async fetchSalesforceAssets() {
    const query = `
      query {
        identity {
          original_name
          function
          active
          description
        }
      }
    `;

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

      const identities = result.data?.identity || [];

      // Define standard headers matching your GraphQL fields
      const headers = ["original_name", "function", "active", "description"];

      // Map the array of objects into rows of simple arrays for ui.js
      const rows = identities.map((item) => [
        item.original_name || "",
        item.function || "",
        String(item.active ?? ""),
        item.description || "",
      ]);

      return { headers, rows };
    } catch (err) {
      console.warn("GraphQL Fetch failed. Using fallback structures:", err);
      return {
        headers: ["original_name", "function", "active", "description"],
        rows: [],
      };
    }
  },

  // Kept here so ui.js doesn't break when clicking the Save button.
  // Replace this placeholder payload structure with your update mutation when ready!
  async saveSalesforceAssets(serializedData) {
    console.log("Save triggered with updated state data:", serializedData);
    alert(
      "Save functionality needs a corresponding GraphQL Mutation implementation.",
    );
    return false;
  },

  // Minimal mock implementation because ui.js explicitly calls serializeCSV before saving
  serializeCSV(headers, rows) {
    return { headers, rows };
  },
};
