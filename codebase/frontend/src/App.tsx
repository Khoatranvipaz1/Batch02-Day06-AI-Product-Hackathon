import { useEffect, useMemo, useState, useRef } from "react";
import { fetchMenuItems, resolveAssetUrl, sendChatMessage } from "./api";
import type { MenuItem, RecommendationItem } from "./api";
import "./styles.css";

type CategoryTile = {
  name: string;
  imageUrl: string;
};

const priceFormatter = new Intl.NumberFormat("vi-VN");

const fallbackCategoryImages = [
  "https://images.unsplash.com/photo-1512058564366-18510be2db19?auto=format&fit=crop&w=300&q=80",
  "https://images.unsplash.com/photo-1572490122747-3968b75cc699?auto=format&fit=crop&w=300&q=80",
  "https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&w=300&q=80",
  "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=300&q=80",
  "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=300&q=80",
  "https://images.unsplash.com/photo-1625944525533-473f1a3d54e7?auto=format&fit=crop&w=300&q=80",
  "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=300&q=80",
  "https://images.unsplash.com/photo-1562967914-608f82629710?auto=format&fit=crop&w=300&q=80",
  "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?auto=format&fit=crop&w=300&q=80"
];

function formatPrice(value: number) {
  return `${priceFormatter.format(value)}d`;
}

function formatSold(value: number) {
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}k sold`;
  }

  return `${value} sold`;
}

export default function App() {
  const [items, setItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState("all");
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);
  const [cartCount, setCartCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  // Chatbot states
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<Array<{
    id: string;
    sender: "user" | "bot";
    text: string;
    timestamp: Date;
    warnings?: string[];
    recommendations?: RecommendationItem[];
  }>>([
    {
      id: "greeting",
      sender: "bot",
      text: "Xin chào! Mình là Trợ lý AI ShopeeFood. Bạn cần mình gợi ý món ăn gì hôm nay? 😋\n\nVí dụ:\n• 'Tìm món ăn trưa dưới 50k không cay'\n• 'Ăn gì tốt cho sức khỏe'\n• 'Gợi ý món gà rán giao nhanh dưới 30 phút'",
      timestamp: new Date()
    }
  ]);
  const [isBotTyping, setIsBotTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, isBotTyping, isChatOpen]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || isBotTyping) return;

    const userText = chatInput.trim();
    setChatInput("");

    const userMsg = {
      id: `user-${Date.now()}`,
      sender: "user" as const,
      text: userText,
      timestamp: new Date()
    };

    setChatMessages((prev) => [...prev, userMsg]);
    setIsBotTyping(true);

    try {
      const response = await sendChatMessage(userText);
      const botMsg = {
        id: `bot-${Date.now()}`,
        sender: "bot" as const,
        text: response.reply,
        timestamp: new Date(),
        warnings: response.warnings,
        recommendations: response.recommendations
      };
      setChatMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = {
        id: `bot-err-${Date.now()}`,
        sender: "bot" as const,
        text: "Xin lỗi, đã có lỗi xảy ra khi kết nối với trợ lý AI. Vui lòng thử lại sau!",
        timestamp: new Date()
      };
      setChatMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsBotTyping(false);
    }
  };

  useEffect(() => {
    let isMounted = true;

    async function loadMenu() {
      try {
        const data = await fetchMenuItems();

        if (!isMounted) {
          return;
        }

        setItems(data.items);
        setCategories(data.categories);
      } catch (caughtError) {
        if (isMounted) {
          setError(
            caughtError instanceof Error
              ? caughtError.message
              : "Không tải được dữ liệu món ăn"
          );
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadMenu();

    return () => {
      isMounted = false;
    };
  }, []);

  const filteredItems = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase("vi-VN");

    return items
      .filter((item) => {
        const matchesCategory =
          activeCategory === "all" || item.category_name === activeCategory;
        const matchesQuery =
          !normalizedQuery ||
          item.name.toLocaleLowerCase("vi-VN").includes(normalizedQuery) ||
          item.shop_name.toLocaleLowerCase("vi-VN").includes(normalizedQuery) ||
          item.description.toLocaleLowerCase("vi-VN").includes(normalizedQuery);

        return matchesCategory && matchesQuery;
      })
      .sort((first, second) => second.sold_count - first.sold_count);
  }, [activeCategory, items, query]);

  const bestSellers = useMemo(
    () =>
      [...items]
        .sort(
          (first, second) =>
            second.sold_count - first.sold_count ||
            second.rating_avg - first.rating_avg
        )
        .slice(0, 4),
    [items]
  );

  const categoryTiles = useMemo<CategoryTile[]>(() => {
    return categories.map((categoryName, index) => {
      const itemForCategory = items.find(
        (item) => item.category_name === categoryName && item.image_url
      );

      return {
        name: categoryName,
        imageUrl: itemForCategory
          ? resolveAssetUrl(itemForCategory.image_url)
          : fallbackCategoryImages[index % fallbackCategoryImages.length]
      };
    });
  }, [categories, items]);

  function addToCart() {
    setCartCount((count) => count + 1);
  }

  return (
    <main className="app">
      <header className="site-header">
        <button className="brand" type="button" onClick={() => setActiveCategory("all")}>
          <span className="brand-mark">SF</span>
          <span>ShopeeFood</span>
        </button>

        <button className="location-pill" type="button">
          <span>⌖</span>
          Deliver to: <strong>123 District 1, HCMC</strong>
        </button>

        <label className="search-box">
          <span>⌕</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search for dishes or restaurants"
          />
        </label>

        <button className="cart-icon" type="button" aria-label="Cart">
          🛒<span>{cartCount}</span>
        </button>
      </header>

      <section className="hero-strip" aria-label="ShopeeFood promotion">
        <div>
          <p>Limited ShopeeFood Deal</p>
          <h1>Đặt món nhanh, chọn quán ngon quanh Quận 1</h1>
          <button type="button">Khám phá ngay</button>
        </div>
      </section>

      <section className="category-section" aria-labelledby="category-title">
        <div className="section-heading">
          <h2 id="category-title">Khám phá danh mục</h2>
          <button type="button" onClick={() => setActiveCategory("all")}>
            View All
          </button>
        </div>

        <div className="category-scroller">
          <button
            className={activeCategory === "all" ? "category-card active" : "category-card"}
            type="button"
            onClick={() => setActiveCategory("all")}
          >
            <img 
              src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=300&q=80" 
              alt="Tất cả" 
            />
            <span>Tất cả</span>
          </button>
          {categoryTiles.map((category) => (
            <button
              className={activeCategory === category.name ? "category-card active" : "category-card"}
              key={category.name}
              type="button"
              onClick={() => setActiveCategory(category.name)}
            >
              <img src={category.imageUrl} alt={category.name} />
              <span>{category.name}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="best-sellers" aria-labelledby="best-sellers-title">
        <div className="section-heading">
          <div>
            <h2 id="best-sellers-title">Today's Best Sellers</h2>
            <p>Highly rated dishes near you</p>
          </div>
          <div className="slider-actions" aria-hidden="true">
            <button type="button">‹</button>
            <button type="button">›</button>
          </div>
        </div>

        {isLoading && <p className="status-text">Đang tải món ăn...</p>}
        {error && <p className="status-text error">{error}</p>}

        {!isLoading && !error && (
          <div className="seller-grid">
            {bestSellers.map((item, index) => (
              <FoodCard
                badge={index === 0 ? "Promo Partner" : index === 1 ? "Flash Sale" : index === 3 ? "Verified" : ""}
                item={item}
                key={item.id}
                onAdd={addToCart}
                onOpen={() => setSelectedItem(item)}
              />
            ))}
          </div>
        )}
      </section>

      {!isLoading && !error && (
        <section className="all-items" aria-labelledby="all-items-title">
          <div className="section-heading">
            <div>
              <h2 id="all-items-title">
                {activeCategory === "all" ? "Tất cả món ngon" : activeCategory}
              </h2>
              <p>{filteredItems.length} món phù hợp</p>
            </div>
          </div>

          <div className="compact-grid">
            {filteredItems.map((item) => (
              <FoodCard
                item={item}
                key={item.id}
                onAdd={addToCart}
                onOpen={() => setSelectedItem(item)}
              />
            ))}
          </div>
        </section>
      )}

      {!isLoading && !error && filteredItems.length === 0 && (
        <p className="status-text">Không có món phù hợp với tìm kiếm hiện tại.</p>
      )}

      {selectedItem && (
        <div className="modal-backdrop" role="presentation">
          <section className="detail-modal" role="dialog" aria-modal="true">
            <button
              className="close-button"
              type="button"
              aria-label="Đóng chi tiết"
              onClick={() => setSelectedItem(null)}
            >
              ×
            </button>
            <div className="modal-image-container">
              <img
                src={resolveAssetUrl(selectedItem.image_url)}
                alt={selectedItem.name}
              />
              {selectedItem.is_signature && <span className="modal-signature-badge">★ Signature</span>}
              {selectedItem.is_combo && <span className="modal-combo-badge">Combo đặc biệt</span>}
            </div>
            <div className="detail-content">
              <span className="modal-category">{selectedItem.category_name}</span>
              <h2>{selectedItem.name}</h2>
              <span className="modal-shop-name">🏪 {selectedItem.shop_name}</span>
              
              <div className="detail-grid">
                <span className="modal-rating">★ {selectedItem.rating_avg.toFixed(1)}</span>
                <span>⏱️ {selectedItem.prepare_time_min} phút</span>
                <span>📈 {formatSold(selectedItem.sold_count)}</span>
                <span>👤 {selectedItem.portion_size}</span>
                {selectedItem.calories_estimate > 0 && (
                  <span className="modal-calories">🔥 {selectedItem.calories_estimate} kcal</span>
                )}
                {selectedItem.spicy_level > 0 && (
                  <span className="modal-spicy">🌶️ Cay: {"🌶️".repeat(selectedItem.spicy_level)}</span>
                )}
              </div>

              <div className="modal-desc-container">
                <h3>Mô tả món ăn</h3>
                <p>{selectedItem.description || "Không có mô tả cho món ăn này."}</p>
              </div>

              <div className="modal-actions">
                <div className="modal-price-container">
                  <div className="modal-price-row">
                    <strong className="modal-effective-price">{formatPrice(selectedItem.effective_price)}</strong>
                    {selectedItem.base_price > selectedItem.effective_price && (
                      <span className="modal-base-price">{formatPrice(selectedItem.base_price)}</span>
                    )}
                  </div>
                  {selectedItem.base_price > selectedItem.effective_price && (
                    <span className="modal-discount-tag">
                      Tiết kiệm {formatPrice(selectedItem.base_price - selectedItem.effective_price)} (-{Math.round(((selectedItem.base_price - selectedItem.effective_price) / selectedItem.base_price) * 100)}%)
                    </span>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => {
                    addToCart();
                    setSelectedItem(null);
                  }}
                >
                  Thêm vào giỏ hàng
                </button>
              </div>
            </div>
          </section>
        </div>
      )}

      {/* Chatbot floating widget */}
      {isChatOpen ? (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <div className="chatbot-header-info">
              <span className="chatbot-avatar">🤖</span>
              <div>
                <h4>Trợ lý ShopeeFood AI</h4>
                <span className="chatbot-status"><span className="status-dot"></span> Đang trực tuyến</span>
              </div>
            </div>
            <button className="chatbot-close-btn" type="button" onClick={() => setIsChatOpen(false)}>×</button>
          </div>

          <div className="chatbot-messages">
            {chatMessages.map((msg) => (
              <div key={msg.id} className={`chatbot-msg-row ${msg.sender}`}>
                {msg.sender === "bot" && <span className="chatbot-msg-avatar">🤖</span>}
                <div className="chatbot-msg-bubble">
                  <div className="chatbot-msg-text">{msg.text}</div>
                  
                  {msg.warnings && msg.warnings.length > 0 && (
                    <div className="chatbot-warnings">
                      {msg.warnings.map((warn, i) => (
                        <div key={i} className="chatbot-warning-badge">⚠️ {warn}</div>
                      ))}
                    </div>
                  )}

                  {msg.recommendations && msg.recommendations.length > 0 && (
                    <div className="chatbot-recommendations">
                      {msg.recommendations.map((rec) => {
                        const fullItem = items.find((i) => i.id === rec.item_id);
                        return (
                          <div key={rec.item_id} className="chatbot-rec-card">
                            {fullItem && (
                              <img 
                                src={resolveAssetUrl(fullItem.image_url)} 
                                alt={rec.item_name} 
                                className="chatbot-rec-img"
                                onClick={() => setSelectedItem(fullItem)}
                              />
                            )}
                            <div className="chatbot-rec-details">
                              <h5 onClick={() => fullItem && setSelectedItem(fullItem)}>{rec.item_name}</h5>
                              <p className="chatbot-rec-shop">{rec.shop_name}</p>
                              <div className="chatbot-rec-meta">
                                <span className="rating">★ {rec.item_rating.toFixed(1)}</span>
                                <span>•</span>
                                <span>{rec.delivery_time_min} phút</span>
                              </div>
                              {rec.reasons && rec.reasons.length > 0 && (
                                <ul className="chatbot-rec-reasons">
                                  {rec.reasons.slice(0, 2).map((reason, idx) => (
                                    <li key={idx}>{reason}</li>
                                  ))}
                                </ul>
                              )}
                              <div className="chatbot-rec-actions">
                                <span className="price">{formatPrice(rec.effective_price)}</span>
                                <div className="buttons">
                                  <button 
                                    type="button" 
                                    className="view-btn" 
                                    onClick={() => fullItem && setSelectedItem(fullItem)}
                                  >
                                    Xem
                                  </button>
                                  <button 
                                    type="button" 
                                    className="add-btn-small" 
                                    onClick={() => {
                                      addToCart();
                                    }}
                                  >
                                    + Giỏ
                                  </button>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isBotTyping && (
              <div className="chatbot-msg-row bot">
                <span className="chatbot-msg-avatar">🤖</span>
                <div className="chatbot-msg-bubble typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="chatbot-input-area" onSubmit={handleSendMessage}>
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Hỏi trợ lý món ăn..."
              disabled={isBotTyping}
            />
            <button type="submit" disabled={!chatInput.trim() || isBotTyping}>
              ➔
            </button>
          </form>
        </div>
      ) : (
        <button className="chatbot-fab" type="button" onClick={() => setIsChatOpen(true)} aria-label="Mở Chatbot AI">
          <span className="chatbot-fab-icon">🤖</span>
          <span className="chatbot-fab-glow"></span>
        </button>
      )}
    </main>
  );
}

function FoodCard({
  badge = "",
  item,
  onAdd,
  onOpen
}: {
  badge?: string;
  item: MenuItem;
  onAdd: () => void;
  onOpen: () => void;
}) {
  const hasDiscount = item.base_price > item.effective_price;
  const discountPercentage = hasDiscount 
    ? Math.round(((item.base_price - item.effective_price) / item.base_price) * 100)
    : 0;
  const badges = badge ? badge.split(" ") : [];

  return (
    <article className="food-card">
      <div className="card-media">
        <button className="image-button" type="button" onClick={onOpen}>
          <img src={resolveAssetUrl(item.image_url)} alt={item.name} />
        </button>

        {(badges.length > 0 || item.is_signature || item.is_combo) && (
          <div className="food-card-badges">
            {badges.map((label, index) => (
              <span
                className={index % 2 === 0 ? "deal-badge" : "partner-badge"}
                key={`${item.id}-${label}`}
              >
                {label}
              </span>
            ))}
            {item.is_signature && <span className="signature-badge">Signature</span>}
            {item.is_combo && <span className="combo-badge">Combo</span>}
          </div>
        )}

        <button className="quick-add-button" type="button" onClick={onAdd} title="Thêm vào giỏ hàng">
          +
        </button>
      </div>

      <div className="food-card-body">
        <h3 className="food-title" onClick={onOpen}>{item.name}</h3>

        <div className="meta-row">
          <span className="rating-span">★ {item.rating_avg.toFixed(1)}</span>
          <span>•</span>
          <span>{item.prepare_time_min} mins</span>
        </div>

        <div className="price-row">
          <div className="price-container">
            <strong className="effective-price">{formatPrice(item.effective_price)}</strong>
            {hasDiscount && (
              <div className="discount-group">
                <span className="base-price">{formatPrice(item.base_price)}</span>
                <span className="discount-pct">-{discountPercentage}%</span>
              </div>
            )}
          </div>
          <span className="sold-count">{formatSold(item.sold_count)}</span>
        </div>
      </div>
    </article>
  );
}
