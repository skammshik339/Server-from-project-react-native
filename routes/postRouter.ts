import express from "express";
import { uploadPostImage } from "../config/multerPost";
import { authMiddleware } from "../middleware/auth";
import {
  createPost,
  getAllPosts,
  getUserPosts,
  toggleLike,
  deletePost,
  getUserPostsById,
} from "../controllers/postsController";

const router = express.Router();

router.post("/", authMiddleware, uploadPostImage.single("image"), createPost);
router.get("/", authMiddleware, getAllPosts);
router.get("/my", authMiddleware, getUserPosts);
router.post("/:postId/like", authMiddleware, toggleLike);
router.delete("/:postId", authMiddleware, deletePost);
router.get("/user/:userId", authMiddleware, getUserPostsById);

export default router;
