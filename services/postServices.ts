import path from 'path'
import Post from "../models/postModel";
import User from "../models/User";
import fs from 'fs'

class PostService {
 async createPost(
  userId: string,
  title: string,
  description: string,
  image: string | null = null,
  transpositionId: string | null = null, 
) {
  const post = new Post({
    userId,
    title,
    description,
    image,
    transpositionId,                          
    likes: []
  });

  await post.save();

console.log('Saving image path in DB:', image);
console.log('Full file system path:', path.join(__dirname, '..', image as string));
console.log('File exists after save:', fs.existsSync(path.join(__dirname, '..', image as string)));

  const pPost = await Post.findById(post._id)
    .populate("userId", "name email image")
    .populate("transpositionId", "name images") 

  return pPost;
}
  async getAllPosts() {
    const posts = await Post.find()
    .sort({ createdAt: -1 })
    .populate("userId", "name email image")
    .populate("transpositionId", "name images")
    

    return posts;
  }

  async getUserPosts(userId: string) {
     const posts = await Post.find({ userId })
    .sort({ createdAt: -1 })
    .populate("userId", "name email image")
    .populate("transpositionId", "name images")  

    return posts;
  }
  async toggleLike(postId: string, userId: string) {
    const post = await Post.findById(postId);
    if (!post) {
      throw new Error("Пост не найден");
    }

    const userIdStr = userId.toString();
    const hasLiked = post.likes.some((id) => id.toString() === userIdStr);

    if (hasLiked) {
      post.likes = post.likes.filter((id) => id.toString() !== userIdStr);
    } else {
      post.likes.push(userId as any);
    }

    await post.save();

    return {
      likesCount: post.likes.length,
      isLiked: !hasLiked,
    };
  }
 async deletePost(postId: string, userId: string) {
  const post = await Post.findById(postId);
  if (!post) {
    throw new Error("Пост не найден");
  }

  if (post.image) {
    const imagePath = path.join(__dirname, '../', post.image);
    if (fs.existsSync(imagePath)) {
      fs.unlinkSync(imagePath);
    }
  }

  await Post.findByIdAndDelete(postId);
  return { message: "Пост удалён" };
}
async getUserPostsById(userId: string) {
  const user = await User.findById(userId);
  if (!user) throw new Error("Пользователь не найден");

  const posts = await Post.find({ userId })
    .sort({ createdAt: -1 })
    .populate("userId", "name email image")
    .populate("transpositionId", "name images")

  return posts;
}
}

export default new PostService();
