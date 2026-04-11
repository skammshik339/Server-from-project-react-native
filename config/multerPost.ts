import multer from 'multer';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import fs from 'fs';

const postsUploadDir = path.join(__dirname, '../uploads/posts');
if (!fs.existsSync(postsUploadDir)) {
  fs.mkdirSync(postsUploadDir, { recursive: true });
}

const postStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, postsUploadDir);
  },
  filename: (req, file, cb) => {
    const fileExt = path.extname(file.originalname);
    const fileName = `${uuidv4()}${fileExt}`;
    cb(null, fileName);
  }
});

export const uploadPostImage = multer({ storage: postStorage });