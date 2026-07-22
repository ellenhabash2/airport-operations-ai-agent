import type {
  ConversationDetail,
  Flight,
  Gate,
  Incident,
  Runway,
  Terminal,
  ToolCall,
  User,
  WeatherReport,
} from "../types/api";

export const mockUser: User = {
  id: 7,
  username: "operator",
  email: "operator@airport.test",
  created_at: "2026-07-22T08:00:00+00:00",
};

export const mockToolCalls: ToolCall[] = [
  {
    tool: "get_flight_by_number",
    arguments: { flight_number: "PW2018" },
    failed: false,
  },
  {
    tool: "get_available_gates",
    arguments: { terminal: "A" },
    failed: true,
    error: "Gate service unavailable",
  },
];

export const mockFlight: Flight = {
  id: 18,
  flight_number: "PW2018",
  airline_name: "Palestinian Wings",
  aircraft_registration: "E4-PW18",
  aircraft_type: "Airbus A320",
  gate_number: "A04",
  terminal: "Terminal A",
  runway_code: "08L/26R",
  origin: "AMM",
  destination: "CDG",
  departure_time: "2026-07-22T10:30:00+00:00",
  arrival_time: "2026-07-22T14:35:00+00:00",
  status: "delayed",
};

export const mockGate: Gate = {
  id: 4,
  gate_number: "A04",
  terminal: "Terminal A",
  status: "occupied",
};

export const mockRunway: Runway = {
  id: 1,
  runway_code: "08L/26R",
  status: "available",
  length: 4100,
};

export const mockTerminal: Terminal = {
  id: 1,
  name: "Terminal A",
  capacity: 18000,
  total_gates: 1,
  available_gates: 0,
  available_gate_numbers: [],
};

export const mockWeather: WeatherReport = {
  id: 1,
  condition: "partly cloudy",
  visibility: 8.5,
  wind_speed: 12,
  temperature: 24,
  created_at: "2026-07-22T09:00:00+00:00",
};

export const mockIncident: Incident = {
  id: 3,
  title: "PW2018 baggage inspection",
  description: "Inspection affecting flight PW2018.",
  severity: "medium",
  location: "Gate A04",
  status: "open",
  created_at: "2026-07-22T09:15:00+00:00",
};

export const mockConversation: ConversationDetail = {
  id: 12,
  title: "Flight PW2018 status",
  message_count: 3,
  created_at: "2026-07-22T08:00:00+00:00",
  updated_at: "2026-07-22T08:05:00+00:00",
  messages: [
    {
      id: 1,
      role: "user",
      text: "Check flight PW2018",
      tool_calls: [],
      created_at: "2026-07-22T08:00:00+00:00",
    },
    {
      id: 2,
      role: "model",
      text: "PW2018 is delayed.\nGate staff have been notified.",
      tool_calls: mockToolCalls,
      created_at: "2026-07-22T08:01:00+00:00",
    },
    {
      id: 3,
      role: "model",
      text: "This is an older message.",
      tool_calls: undefined as unknown as ToolCall[],
      created_at: "2026-07-22T08:02:00+00:00",
    },
  ],
};
