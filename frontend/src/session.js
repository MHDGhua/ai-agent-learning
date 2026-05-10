import { computed, ref } from "vue";

import { authApi } from "./api";

export const sessionKey = Symbol("lerap-session");

const user = ref(null);
const sessionLoaded = ref(false);
const sessionLoading = ref(false);
const sessionError = ref("");
let pendingSessionRequest = null;

function applySessionUser(nextUser) {
  user.value = nextUser || null;
  sessionLoaded.value = true;
}

async function refreshSession(options = {}) {
  if (sessionLoaded.value && !options.force) {
    return user.value;
  }

  if (pendingSessionRequest) {
    return pendingSessionRequest;
  }

  sessionLoading.value = true;
  sessionError.value = "";
  pendingSessionRequest = authApi
    .session()
    .then((response) => {
      applySessionUser(response?.user || null);
      return user.value;
    })
    .catch((error) => {
      user.value = null;
      sessionLoaded.value = true;
      sessionError.value = error?.message || "无法获取登录状态。";
      return null;
    })
    .finally(() => {
      sessionLoading.value = false;
      pendingSessionRequest = null;
    });

  return pendingSessionRequest;
}

function setUser(nextUser) {
  applySessionUser(nextUser);
}

function clearUser() {
  user.value = null;
  sessionLoaded.value = true;
}

export function createSessionState() {
  return {
    user,
    sessionLoaded,
    sessionLoading,
    sessionError,
    isAuthenticated: computed(() => Boolean(user.value)),
    refreshSession,
    setUser,
    clearUser,
  };
}
