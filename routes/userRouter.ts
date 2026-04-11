import express from "express";
import { updateProfile, removeImage, updatePrivacy, getProfile } from "../controllers/userController";
import { authMiddleware } from "../middleware/auth";
const router = express.Router();
router.put("/profile", authMiddleware, updateProfile);
router.delete("/image", authMiddleware, removeImage);
router.put('/privacy', authMiddleware, updatePrivacy);
router.get('/:id', authMiddleware, getProfile);
export default router;
