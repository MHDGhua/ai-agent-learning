const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, status = 500) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof payload === "object" && payload !== null && "detail" in payload
        ? payload.detail
        : "请求失败";
    throw new ApiError(String(detail), response.status);
  }

  return payload;
}

export const authApi = {
  register(body) {
    return apiRequest("/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  login(body) {
    return apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  logout() {
    return apiRequest("/auth/logout", { method: "POST" });
  },
  me() {
    return apiRequest("/auth/me");
  },
  changePassword(body) {
    return apiRequest("/auth/change-password", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};

export const arbitrationApi = {
  workup(body) {
    return apiRequest("/arbitration/workup", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  generateDocument(body) {
    return apiRequest("/arbitration/generate-document", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  validateDocument(body) {
    return apiRequest("/arbitration/validate-document", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};

export const workspaceApi = {
  listCases() {
    return apiRequest("/workspace/cases");
  },
  saveCase(body) {
    return apiRequest("/workspace/cases", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
  getCase(caseId) {
    return apiRequest(`/workspace/cases/${caseId}`);
  },
  deleteCase(caseId) {
    return apiRequest(`/workspace/cases/${caseId}`, {
      method: "DELETE",
    });
  },
  listActivities(limit = 12) {
    return apiRequest(`/workspace/activities?limit=${limit}`);
  },
};
