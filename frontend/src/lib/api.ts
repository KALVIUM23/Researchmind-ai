const API_BASE_URL = "http://localhost:8000/api/v1";

export interface Document {
  id: string;
  filename: string;
}

export const uploadDocument = async (file: File): Promise<{ document_id: string, message: string }> => {
  const formData = new FormData();
  formData.append("file", file);
  
  const token = localStorage.getItem("token");

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to upload document");
  }

  return response.json();
};

export const generateSummary = async (document_id: string, length: string = "medium") => {
  const token = localStorage.getItem("token");
  const response = await fetch(`${API_BASE_URL}/documents/summary`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ document_id, length }),
  });

  if (!response.ok) {
    throw new Error("Failed to generate summary");
  }

  return response; // Return raw response for streaming
};

export const generateResearchNotes = async (document_id: string, topic?: string) => {
  const token = localStorage.getItem("token");
  const response = await fetch(`${API_BASE_URL}/documents/research-notes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ document_id, topic }),
  });

  if (!response.ok) {
    throw new Error("Failed to generate research notes");
  }

  return response.json();
};

// Streaming API call for chat handled directly in the component using EventSource or fetch
