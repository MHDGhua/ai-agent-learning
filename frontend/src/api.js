const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, status = 500) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function formatErrorDetail(detail) {
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item && typeof item === "object") {
          const location = Array.isArray(item.loc) ? item.loc.filter((part) => part !== "body").join(".") : "";
          const message = item.msg || item.message || "请求参数错误";
          return location ? `${location}: ${message}` : message;
        }
        return "";
      })
      .filter(Boolean);
    return messages.join("；") || "请求参数错误";
  }
  if (detail && typeof detail === "object") {
    return detail.message || detail.error || JSON.stringify(detail);
  }
  return "请求失败";
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
    const detail = typeof payload === "object" && payload !== null && "detail" in payload ? payload.detail : payload;
    throw new ApiError(formatErrorDetail(detail), response.status);
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
  session() {
    return apiRequest("/auth/session");
  },
  updateProfile(body) {
    return apiRequest("/auth/profile", {
      method: "PUT",
      body: JSON.stringify(body),
    });
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
  importLegacy(body) {
    return apiRequest("/workspace/import-legacy", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};
