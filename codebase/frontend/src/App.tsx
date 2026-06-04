import { useEffect, useMemo, useState } from "react";
import { fetchMenuItems, MenuItem, resolveAssetUrl } from "./api";
import "./styles.css";

type SortMode = "popular" | "rating" | "priceAsc" | "priceDesc";

const priceFormatter = new Intl.NumberFormat("vi-VN");

function formatPrice(value: number) {
  return `${priceFormatter.format(value)}d`;
}

function formatSold(value: number) {
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}k`;
  }

  return value.toString();
}

export default function App() {
  const [items, setItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [sortMode, setSortMode] = useState<SortMode>("popular");
  const [maxPrice, setMaxPrice] = useState(120000);
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);
  const [likedIds, setLikedIds] = useState<Set<string>>(() => new Set());
  const [cartCount, setCartCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

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
        const highestPrice = Math.max(
          ...data.items.map((item) => item.effective_price),
          120000
        );
        setMaxPrice(Math.ceil(highestPrice / 10000) * 10000);
      } catch (caughtError) {
        if (isMounted) {
          setError(
            caughtError instanceof Error
              ? caughtError.message
              : "Khong tai duoc du lieu mon an"
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
    const result = items.filter((item) => {
      const matchesCategory =
        category === "all" || item.category_name === category;
      const matchesPrice = item.effective_price <= maxPrice;
      const matchesQuery =
        !normalizedQuery ||
        item.name.toLocaleLowerCase("vi-VN").includes(normalizedQuery) ||
        item.shop_name.toLocaleLowerCase("vi-VN").includes(normalizedQuery) ||
        item.description.toLocaleLowerCase("vi-VN").includes(normalizedQuery);

      return matchesCategory && matchesPrice && matchesQuery;
    });

    return [...result].sort((first, second) => {
      if (sortMode === "rating") {
        return second.rating_avg - first.rating_avg;
      }

      if (sortMode === "priceAsc") {
        return first.effective_price - second.effective_price;
      }

      if (sortMode === "priceDesc") {
        return second.effective_price - first.effective_price;
      }

      return second.sold_count - first.sold_count;
    });
  }, [category, items, maxPrice, query, sortMode]);

  const featuredItems = useMemo(
    () => filteredItems.filter((item) => item.is_signature).slice(0, 4),
    [filteredItems]
  );

  const averagePrice = useMemo(() => {
    if (filteredItems.length === 0) {
      return 0;
    }

    const total = filteredItems.reduce(
      (sum, item) => sum + item.effective_price,
      0
    );
    return Math.round(total / filteredItems.length);
  }, [filteredItems]);

  function toggleLike(itemId: string) {
    setLikedIds((current) => {
      const next = new Set(current);

      if (next.has(itemId)) {
        next.delete(itemId);
      } else {
        next.add(itemId);
      }

      return next;
    });
  }

  return (
    <main className="app">
      <header className="topbar">
        <div>
          <p className="eyebrow">ShopeeFood Q1 Mock Menu</p>
          <h1>Khám phá món ngon Quận 1</h1>
        </div>
        <button className="cart-button" type="button">
          Giỏ hàng <span>{cartCount}</span>
        </button>
      </header>

      <section className="menu-controls" aria-label="Bo loc mon an">
        <label className="search-field">
          <span>Tìm kiếm</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Cơm tấm, bún bò, trà sữa..."
          />
        </label>

        <label className="select-field">
          <span>Sắp xếp</span>
          <select
            value={sortMode}
            onChange={(event) => setSortMode(event.target.value as SortMode)}
          >
            <option value="popular">Bán chạy</option>
            <option value="rating">Đánh giá cao</option>
            <option value="priceAsc">Giá thấp trước</option>
            <option value="priceDesc">Giá cao trước</option>
          </select>
        </label>

        <label className="range-field">
          <span>Giá tối đa: {formatPrice(maxPrice)}</span>
          <input
            type="range"
            min="15000"
            max="160000"
            step="5000"
            value={maxPrice}
            onChange={(event) => setMaxPrice(Number(event.target.value))}
          />
        </label>
      </section>

      <nav className="category-tabs" aria-label="Danh muc mon an">
        <button
          className={category === "all" ? "active" : ""}
          type="button"
          onClick={() => setCategory("all")}
        >
          Tất cả
        </button>
        {categories.map((categoryName) => (
          <button
            className={category === categoryName ? "active" : ""}
            key={categoryName}
            type="button"
            onClick={() => setCategory(categoryName)}
          >
            {categoryName}
          </button>
        ))}
      </nav>

      <section className="stats-row" aria-label="Thong ke menu">
        <div>
          <strong>{filteredItems.length}</strong>
          <span>Món phù hợp</span>
        </div>
        <div>
          <strong>{formatPrice(averagePrice)}</strong>
          <span>Giá trung bình</span>
        </div>
        <div>
          <strong>{featuredItems.length}</strong>
          <span>Món signature</span>
        </div>
      </section>

      {isLoading && <p className="status-text">Đang tải món ăn...</p>}
      {error && <p className="status-text error">{error}</p>}

      {!isLoading && !error && (
        <section className="menu-grid" aria-label="Danh sach mon an">
          {filteredItems.map((item) => (
            <article className="menu-card" key={item.id}>
              <button
                className={`like-button ${likedIds.has(item.id) ? "liked" : ""}`}
                type="button"
                aria-label="Luu mon yeu thich"
                onClick={() => toggleLike(item.id)}
              >
                {likedIds.has(item.id) ? "♥" : "♡"}
              </button>

              <button
                className="image-button"
                type="button"
                onClick={() => setSelectedItem(item)}
              >
                <img src={resolveAssetUrl(item.image_url)} alt={item.name} />
              </button>

              <div className="menu-card-body">
                <div className="card-heading">
                  <div>
                    <p>{item.category_name}</p>
                    <h2>{item.name}</h2>
                  </div>
                  {item.is_signature && <span>Signature</span>}
                </div>

                <p className="shop-name">{item.shop_name}</p>

                <div className="meta-row">
                  <span>{item.rating_avg.toFixed(1)} sao</span>
                  <span>{formatSold(item.sold_count)} đã bán</span>
                  <span>{item.prepare_time_min} phút</span>
                </div>

                <div className="price-row">
                  <div>
                    <strong>{formatPrice(item.effective_price)}</strong>
                    {item.sale_price && (
                      <span>{formatPrice(item.base_price)}</span>
                    )}
                  </div>
                  <button type="button" onClick={() => setCartCount((n) => n + 1)}>
                    Thêm
                  </button>
                </div>
              </div>
            </article>
          ))}
        </section>
      )}

      {!isLoading && !error && filteredItems.length === 0 && (
        <p className="status-text">Không có món phù hợp bộ lọc hiện tại.</p>
      )}

      {selectedItem && (
        <div className="modal-backdrop" role="presentation">
          <section className="detail-modal" role="dialog" aria-modal="true">
            <button
              className="close-button"
              type="button"
              aria-label="Dong chi tiet"
              onClick={() => setSelectedItem(null)}
            >
              ×
            </button>
            <img
              src={resolveAssetUrl(selectedItem.image_url)}
              alt={selectedItem.name}
            />
            <div className="detail-content">
              <p className="eyebrow">{selectedItem.category_name}</p>
              <h2>{selectedItem.name}</h2>
              <p>{selectedItem.description}</p>
              <div className="detail-grid">
                <span>{selectedItem.rating_avg.toFixed(1)} sao</span>
                <span>{selectedItem.calories_estimate} kcal</span>
                <span>Cay {selectedItem.spicy_level}/5</span>
                <span>{selectedItem.portion_size}</span>
              </div>
              <div className="modal-actions">
                <strong>{formatPrice(selectedItem.effective_price)}</strong>
                <button
                  type="button"
                  onClick={() => {
                    setCartCount((n) => n + 1);
                    setSelectedItem(null);
                  }}
                >
                  Thêm vào giỏ
                </button>
              </div>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
