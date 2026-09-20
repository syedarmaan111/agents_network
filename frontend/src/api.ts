export type ChatbotType = "engineer" | "doctor" | "lawyer";

export interface TokenResponse { access_token: string; token_type: string }
export interface UserResponse { id: number; email: string; created_at: string }
export interface ChatResponse { error: boolean; conversation_id: number; chatbot_type: ChatbotType; response: string }
export interface ApiError { status: number; message: string }

const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  try {
    const response = await fetch(`${baseUrl}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init.headers },
    });
    let data: unknown;
    try { data = await response.json(); } catch { throw { status: response.status, message: "The server returned an invalid response." } satisfies ApiError; }
    if (!response.ok || (typeof data === "object" && data !== null && "error" in data && data.error)) {
      const message = typeof data === "object" && data !== null && "message" in data && typeof data.message === "string" ? data.message : "Request failed.";
      throw { status: response.status, message } satisfies ApiError;
    }
    return data as T;
  } catch (error) {
    if (typeof error === "object" && error !== null && "message" in error) throw error;
    throw { status: 0, message: "Unable to reach the server. Please try again." } satisfies ApiError;
  }
}

export const api = {
  register: (email: string, password: string) => request<UserResponse>("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) }),
  login: (email: string, password: string) => request<TokenResponse>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  logout: (token: string) => request<{ error: boolean; message: string }>("/auth/logout", { method: "POST" }, token),
  sendChatMessage: (token: string, message: string, conversation_id: number | null, chatbot_type: ChatbotType) => request<ChatResponse>("/chat", { method: "POST", body: JSON.stringify({ message, conversation_id, chatbot_type }) }, token),
};
