import { Link } from 'react-router-dom';

interface Props {
  count: number;
}

export function ReviewBanner({ count }: Props) {
  if (count === 0) return null;
  return (
    <Link to="/review" className="review-banner">
      <span>📋 您有 {count} 条记录待审核</span>
      <span>去审核 →</span>
    </Link>
  );
}
