export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string | null;
}

export interface LoginResponse {
  access_token: string;
  user: User;
}

export interface RegisterResponse {
  message: string;
  user: User;
}

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string | null;
}

export interface LoginResponse {
  access_token: string;
  user: User;
}

export interface RegisterResponse {
  message: string;
  user: User;
}

export interface Flight {
  id: number;
  flight_number: string;
  airline_name: string | null;
  aircraft_registration: string | null;
  aircraft_type: string | null;
  gate_number: string | null;
  terminal: string | null;
  runway_code: string | null;
  origin: string;
  destination: string;
  departure_time: string | null;
  arrival_time: string | null;
  estimated_departure_time?: string | null;
  actual_departure_time?: string | null;
  estimated_arrival_time?: string | null;
  actual_arrival_time?: string | null;
  delay_duration_minutes?: number | null;
  delay_reason?: string | null;
  status: string;
}

export interface Gate {
  id: number;
  gate_number: string;
  terminal: string | null;
  status: string;
}

export interface Terminal {
  id: number;
  name: string;
  capacity: number;
  total_gates: number;
  available_gates: number;
  available_gate_numbers: string[];
}

export interface Runway {
  id: number;
  runway_code: string;
  status: string;
  length: number;
  closure_reason?: string | null;
}

export interface Incident {
  id: number;
  title: string;
  description: string;
  severity: string;
  location: string;
  status?: string | null;
  created_at: string | null;
}

export interface WeatherReport {
  id: number;
  condition: string;
  visibility: number;
  wind_speed: number;
  temperature: number;
  created_at: string | null;
}

/** Every list endpoint wraps its payload in a data key. */
export interface ListResponse<T> {
  data: T[];
}

export interface ToolCall {
  tool: string;
  arguments: Record<string, unknown>;
  failed: boolean;
  error?: string;
}

export interface AgentAnswer {
  answer: string;
  tool_calls: ToolCall[];
  conversation_id: number;
}

export interface ConversationSummary {
  id: number;
  title: string;
  message_count: number;
  created_at: string | null;
  updated_at: string | null;
}

export interface StoredMessage {
  id: number;
  role: string;
  text: string | null;
  tool_calls: ToolCall[];
  created_at: string | null;
}

export interface ConversationDetail extends ConversationSummary {
  messages: StoredMessage[];
}

/** Endpoints that return a single object wrap it in a data key. */
export interface ItemResponse<T> {
  data: T;
}
