import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createSessionState, sessionKey } from "./session";
import "./styles.css";

const app = createApp(App);
const session = createSessionState();

function isAdminUser(user) {
  if (!user) {
    return false;
  }
  return Boolean(user.is_admin || user.role === "管理员" || String(user.role || "").toLowerCase() === "admin");
}

router.beforeEach(async (to) => {
  const currentUser = await session.refreshSession();

  if (to.meta.requiresAuth && !currentUser) {
    return {
      name: "login",
      query: { redirect: to.fullPath },
    };
  }

  if (to.meta.requiresAdmin && !isAdminUser(currentUser)) {
    return { name: "assistant" };
  }

  if (to.meta.guestOnly && currentUser) {
    const redirect = typeof to.query.redirect === "string" ? to.query.redirect : "";
    return redirect.startsWith("/") ? redirect : { name: "assistant" };
  }

  return true;
});

app.provide(sessionKey, session);
app.use(router);
app.mount("#app");
