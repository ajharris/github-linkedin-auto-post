
import axios from "axios";

const API_BASE_URL = "/api/github";

export const fetchGitHubStatus = async (userId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/${userId}/status`);
    return response.data;
  } catch (error) {
    console.error("Error fetching GitHub status:", error);
    throw error;
  }
};

export const fetchGitHubCommits = async (userId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/${userId}/commits`);
    return response.data.commits;
  } catch (error) {
    console.error("Error fetching GitHub commits:", error);
    throw error;
  }
};

export const postCommitToLinkedIn = async (userId, commitId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/${userId}/post_commit`, {
      commit_id: commitId,
    });
    return response.data;
  } catch (error) {
    console.error("Error posting commit to LinkedIn:", error);
    throw error;
  }
};

export const disconnectLinkedIn = async (userId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/${userId}/disconnect_linkedin`);
    return response.data;
  } catch (error) {
    console.error("Error disconnecting LinkedIn:", error);
    throw error;
  }
};