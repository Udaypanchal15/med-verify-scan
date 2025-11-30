export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export async function fetchMedicineInfo(name) {
  const res = await fetch(`${API_BASE_URL}/medicine-info?name=${encodeURIComponent(name)}`);
  if (!res.ok) throw new Error("Failed to fetch medicine info");
  return await res.json();
}

export async function scanQrData(qrData) {
  const res = await fetch(`${API_BASE_URL}/scan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ qr_data: qrData }),
  });
  if (!res.ok) throw new Error("Failed to scan QR");
  return await res.json();
}
