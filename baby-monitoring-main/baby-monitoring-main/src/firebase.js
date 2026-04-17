// src/firebase.js

import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";

const firebaseConfig = {
    apiKey: "AIzaSyD8NaGU3ECD2q0xrb-X3rrU0pi6u-R5rfA",
    authDomain: "baby-detection-c40a9.firebaseapp.com",
    databaseURL: "https://baby-detection-c40a9-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "baby-detection-c40a9",
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

export { db };