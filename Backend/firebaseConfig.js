import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIza....", 
  authDomain: "roomiehaus.firebaseapp.com",
  projectId: "roomiehaus",
  storageBucket: "roomiehaus.appspot.com",
  messagingSenderId: "....",
  appId: "1:...."
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

export { db };
