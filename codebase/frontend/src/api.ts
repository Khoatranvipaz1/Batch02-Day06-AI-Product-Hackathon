/// <reference types="vite/client" />
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type MenuItem = {
  id: string;
  name: string;
  description: string;
  base_price: number;
  sale_price: number | null;
  effective_price: number;
  image_url: string;
  source_image_url: string;
  rating_avg: number;
  rating_count: number;
  sold_count: number;
  prepare_time_min: number;
  spicy_level: number;
  calories_estimate: number;
  portion_size: string;
  is_available: boolean;
  is_signature: boolean;
  is_combo: boolean;
  category_id: string;
  category_name: string;
  shop_id: string;
  shop_name: string;
  shop_rating: number;
  shop_status: string;
};

export type MenuResponse = {
  items: MenuItem[];
  categories: string[];
  total: number;
};

export type RecommendationItem = {
  item_id: string;
  item_name: string;
  shop_name: string;
  category_name: string;
  effective_price: number;
  delivery_fee: number;
  total_price: number;
  delivery_time_min: number;
  item_rating: number;
  shop_rating: number;
  spicy_level: number;
  score: number;
  reasons: string[];
};

export type IntentResponse = Record<string, unknown>;

export type ChatResponse = {
  reply: string;
  intent: IntentResponse;
  clarifying_question: string | null;
  warnings: string[];
  recommendations: RecommendationItem[];
};

export type ChatHistoryMessage = {
  role: "user" | "assistant";
  content: string;
};

export type ChatRequest = {
  message: string;
  history?: ChatHistoryMessage[];
};


export function resolveAssetUrl(path: string) {
  if (path.startsWith("http")) {
    return path;
  }

  return `${API_BASE_URL}${path}`;
}

export async function fetchMenuItems() {
  const params = new URLSearchParams({ limit: "300" });
  const response = await fetch(`${API_BASE_URL}/api/menu-items?${params}`);

  if (!response.ok) {
    throw new Error("Failed to load menu items");
  }

  return response.json() as Promise<MenuResponse>;
}

export async function sendChatMessage(message: string, history: ChatHistoryMessage[] = []) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message, history } satisfies ChatRequest)
  });

  if (!response.ok) {
    throw new Error(`Failed to send chat message: ${response.status}`);
  }

  const data = (await response.json()) as ChatResponse;

  return {
    ...data,
    clarifying_question: data.clarifying_question ?? null,
    warnings: data.warnings ?? [],
    recommendations: data.recommendations ?? []
  };
}
