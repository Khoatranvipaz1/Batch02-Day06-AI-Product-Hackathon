const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

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

  return response.json() as Promise<{ reply: string }>;
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
