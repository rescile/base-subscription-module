// app/navigation.js
window.Navigation = {
  // Just add the new view object right here inside your array:
  menuItems: [
    { id: "identity", label: "Identity", active: true },
    { id: "provider", label: "Provider", active: false },
  ],

  renderSidebar() {
    const navMenu = document.getElementById("nav-menu");
    if (!navMenu) return;

    navMenu.innerHTML = this.menuItems
      .map(
        (item) => `
            <a href="#"
               onclick="Navigation.selectMenu('${item.id}')"
               class="relative flex items-center px-6 py-2.5 text-sm font-medium transition-all duration-150 ${
                 item.active
                   ? "bg-appHover text-appPrimary before:absolute before:left-0 before:top-0 before:bottom-0 before:w-1 before:bg-appPrimary"
                   : "text-appFg/60 hover:bg-appHover/60 hover:text-appFg"
               }">
                ${item.label}
            </a>
        `,
      )
      .join("");
  },

  selectMenu(id) {
    this.menuItems.forEach((item) => (item.active = item.id === id));
    this.renderSidebar();

    if (typeof window.switchView === "function") {
      window.switchView(id);
    }
  },
};
