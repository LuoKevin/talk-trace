type ActionItemsDisplayProps = {
  title: string;
  items: string[];
};

export function ActionItemsDisplay({ title, items }: ActionItemsDisplayProps) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      {items.length > 0 ? (
        <ul className="item-list">
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted">None found yet.</p>
      )}
    </section>
  );
}
