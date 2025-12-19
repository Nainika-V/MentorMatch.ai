const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";

interface RequestOptions extends RequestInit {
  body?: any;
}

async function request(endpoint: string, options: RequestOptions = {}) {
  const { body, ...customConfig } = options;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  const config: RequestInit = {
    method: options.method || (body ? "POST" : "GET"),
    headers: {
      ...headers,
      ...options.headers,
    },
    // Include credentials to send cookies with cross-origin requests
    credentials: "include",
    ...customConfig,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const url = `${BASE_URL}${endpoint}`;
  console.log("Attempting to fetch:", url); // DEBUGGING LINE

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: response.statusText }));
      throw new Error(errorData.message || "An error occurred");
    }

    // For DELETE or other methods that might not return a body
    if (response.status === 204 || response.headers.get("content-length") === "0") {
      return undefined;
    }

    return await response.json();
  } catch (error) {
    console.error("API request error:", error);
    throw error;
  }
}

export const api = {
  get: (endpoint: string, options?: RequestOptions) => request(endpoint, { ...options, method: "GET" }),
  post: (endpoint: string, body: any, options?: RequestOptions) => request(endpoint, { ...options, method: "POST", body }),
  put: (endpoint: string, body: any, options?: RequestOptions) => request(endpoint, { ...options, method: "PUT", body }),
  delete: (endpoint: string, options?: RequestOptions) => request(endpoint, { ...options, method: "DELETE" }),
};
