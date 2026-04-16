export interface NavItem {
  id: string;
  label: string;
  icon: string;
}

export interface MetricCardData {
  title: string;
  value: string;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
  subtext?: string;
  icon?: string;
}

export interface EventLog {
  id: string;
  timestamp: string;
  location: string;
  type: string;
  confidence: string;
  status: 'secured' | 'archived' | 'maintenance' | 'alert';
}
