import { collection, addDoc, getDocs } from "firebase/firestore";
import { db } from "./firebaseConfig.js";

async function addRoommate(name, income) {
  try {
    const docRef = await addDoc(collection(db, "roommates"), {
      name: name,
      income: income
    });
    console.log("Document added with ID: ", docRef.id);
  } catch (e) {
    console.error("Error adding document: ", e);
  }
}

async function getRoommates() {
  const querySnapshot = await getDocs(collection(db, "roommates"));
  querySnapshot.forEach((doc) => {
    console.log(`${doc.id} => `, doc.data());
  });
}

addRoommate("Aura", 10000);
getRoommates();
