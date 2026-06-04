const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

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
  intent: {
    budget: number | null;
    max_delivery_min: number | null;
    no_spicy: boolean;
    lunch: boolean;
    healthy: boolean;
    light: boolean;
    cheap: boolean;
    unclear: boolean;
  };
  clarifying_question: string | null;
  warnings: string[];
  recommendations: RecommendationItem[];
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

  return response.json() as Promise<ChatResponse>;
}

export async function getMenuSummary() {
  const response = await fetch(`${API_BASE_URL}/api/menu/summary`);

  if (!response.ok) {
    throw new Error("Failed to load menu summary");
  }

  return response.json() as Promise<{ items: number; shops: number; categories: number }>;
}
