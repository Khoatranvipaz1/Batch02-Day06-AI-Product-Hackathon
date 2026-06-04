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

export type MenuItemImage = {
  id: string;
  name: string;
  shop_id: string;
  base_price: number;
  sale_price: number | null;
  image_url: string;
  image_source: string;
  image_title: string | null;
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

export type ChatResponse = {
  reply: string;
  intent: Record<string, unknown>;
  clarifying_question: string | null;
  warnings: string[];
  recommendations: RecommendationItem[];
};

export type ChatHistoryMessage = {
  role: "user" | "assistant";
  content: string;
  recommendation_item_ids?: string[];
};

export type ChatRequest = {
  message: string;
  history: ChatHistoryMessage[];
export type ChatRequest = {
  message: string;
};

export type FetchMenuItemsOptions = {
  search?: string;
  category?: string;
  limit?: number;
  offset?: number;
  availableOnly?: boolean;
};

export function resolveAssetUrl(path: string) {
  if (path.startsWith("http")) {
    return path;
  }

  return `${API_BASE_URL}${path}`;
}

export async function fetchMenuItems(options: FetchMenuItemsOptions = {}) {
  const {
    search = "",
    category = "",
    limit = 24,
    offset = 0,
    availableOnly = true
  } = options;
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
    available_only: String(availableOnly)
  });

  if (search.trim()) {
    params.set("search", search.trim());
  }

  if (category.trim() && category !== "all") {
    params.set("category", category.trim());
  }

  const response = await fetch(`${API_BASE_URL}/api/menu-items?${params}`);

  if (!response.ok) {
    throw new Error("Failed to load menu items");
  }

  return response.json() as Promise<MenuResponse>;
}

export async function fetchMenuItem(itemId: string) {
  const response = await fetch(
    `${API_BASE_URL}/api/menu-items/${encodeURIComponent(itemId)}`
  );

  if (!response.ok) {
    throw new Error("Failed to load menu item");
  }

  return response.json() as Promise<MenuItem>;
}

export async function fetchMenuItemImages(query?: string, limit = 20, offset = 0) {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset)
  });

  if (query?.trim()) {
    params.set("query", query.trim());
  }

  const response = await fetch(`${API_BASE_URL}/api/menu-items/images?${params}`);

  if (!response.ok) {
    throw new Error("Failed to fetch menu item images");
  }

  return response.json() as Promise<MenuItemImage[]>;
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
