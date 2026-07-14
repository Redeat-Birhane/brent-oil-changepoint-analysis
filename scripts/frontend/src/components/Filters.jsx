const CATEGORY_COLORS = {
    "Geopolitical Conflict": "#C4574B",
    "Economic Shock": "#4A90A4",
    "OPEC Policy": "#E8974A",
    "Sanctions": "#9B6FC4",
    "Geopolitical Shock": "#C4574B",
    "Market Extreme": "#8B93A1",
};

export default function Filters({ startDate, endDate, onDateChange, categories, activeCategories, onToggleCategory }) {
    return (
        <div className="panel">
            <h3 className="panel-title">Filters</h3>

            <div className="filter-group">
                <label className="filter-label">From</label>
                <input
                    type="date"
                    value={startDate}
                    onChange={(e) => onDateChange(e.target.value, endDate)}
                />
            </div>

            <div className="filter-group">
                <label className="filter-label">To</label>
                <input
                    type="date"
                    value={endDate}
                    onChange={(e) => onDateChange(startDate, e.target.value)}
                />
            </div>

            <div className="filter-group">
                <label className="filter-label">Event categories</label>
                <div>
                    {categories.map((cat) => (
                        <span
                            key={cat}
                            className={`category-chip ${activeCategories.includes(cat) ? "active" : ""}`}
                            onClick={() => onToggleCategory(cat)}
                        >
                            <span
                                className="category-dot"
                                style={{ background: CATEGORY_COLORS[cat] || "#8B93A1" }}
                            />
                            {cat}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
}

export { CATEGORY_COLORS };