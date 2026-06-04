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

export async function sendChatMessage(message: string) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message })
  });

  if (!response.ok) {
    throw new Error("Failed to send chat message");
  }

  return response.json() as Promise<ChatResponse>;
}

export async function getMenuSummary() {
  const response = await fetch(`${API_BASE_URL}/api/menu/summary`);

  if (!response.ok) {
    throw new Error("Failed to load menu summary");
  }

  return response.json() as Promise<{ items: number; shops: number; categories: number }>;
}
