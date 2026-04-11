import { Request, Response } from 'express';
import postService from '../services/postServices';

export const createPost = async (req: any, res: Response) => {
  try {
    const userId = req.user?._id;
    const { title, description, transpositionId } = req.body;  
    const image = req.file ? `/uploads/posts/${req.file.filename}` : null;

    if (!title || !description) {
      return res.status(400).json({ error: 'Заполните все поля' });
    }

    const post = await postService.createPost(
      userId, 
      title, 
      description, 
      image, 
      transpositionId || null                  
    );

    res.status(201).json({
      message: 'Пост создан',
      post
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};


export const getAllPosts = async (req: Request, res: Response) => {
  try {
    const posts = await postService.getAllPosts();

    res.json({ posts });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

export const getUserPosts = async (req: any, res: Response) => {
  try {
    const userId = req.user?._id;

    const posts = await postService.getUserPosts(userId);

    res.json({ posts });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
};

export const toggleLike = async (req: any, res: Response) => {
  try {
    const userId = req.user?._id;
    const { postId } = req.params;

    const result = await postService.toggleLike(postId, userId);

    res.json(result);
  } catch (error: any) {
    if (error.message === 'Пост не найден') {
      return res.status(404).json({ error: error.message });
    }
    res.status(500).json({ error: error.message });
  }
};

export const deletePost = async (req: any, res: Response) => {
  try {
    const userId = req.user?._id;
    const { postId } = req.params;

    const result = await postService.deletePost(postId, userId);

    res.json(result);
  } catch (error: any) {
    if (error.message === 'Пост не найден') {
      return res.status(404).json({ error: error.message });
    }
    res.status(500).json({ error: error.message });
  }
};

export const getUserPostsById = async (req: any, res: Response) => {
  try {
    const userId = req.params.userId;

    const posts = await postService.getUserPostsById(userId);
    res.json({ posts });
  } catch (error: any) {
    if (error.message === "Пользователь не найден") {
      return res.status(404).json({ error: error.message });
    }
    res.status(500).json({ error: error.message });
  }
};