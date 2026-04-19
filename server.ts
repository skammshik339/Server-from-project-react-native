import dotenv from "dotenv";
dotenv.config();

import express from "express";
import mongoose from "mongoose";
import cors from "cors";
import cookieParser from "cookie-parser";
import path from "path";

import authRoutes from "./routes/authRouter";
import transposeRouter from "./routes/transposeRouter";
import userRouter from "./routes/userRouter";
import postRouter from "./routes/postRouter";

import rateLimit from "express-rate-limit";

const PORT = process.env.PORT || 3000;
const app = express();

app.set("trust proxy", 1);

// Определяем пути в зависимости от окружения
const isProduction = process.env.NODE_ENV === 'production';

const uploadsPath = isProduction
  ? path.join(__dirname, '../uploads')
  : path.join(__dirname, 'uploads');

const outputsPath = isProduction
  ? path.join(__dirname, '../outputs')
  : path.join(__dirname, 'outputs');

// CORS настройки
const corsOptions = {
  origin: "*",
  credentials: true,
  exposedHeaders: ["Authorization", "X-Refresh-Token", "X-New-Access-Token"],
  allowedHeaders: ["Content-Type", "Authorization", "X-Refresh-Token"],
};
app.use(cors(corsOptions));

app.use(express.json());
app.use(cookieParser());

// Статические файлы
app.use("/uploads", express.static(uploadsPath));
app.use("/outputs", express.static(outputsPath));

// Rate limiting
const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 50,
  message: {
    error: "Too many requests",
    message: "Превышен лимит запросов",
  },
});
app.use(limiter);

// Роуты
app.use("/api/auth", authRoutes);
app.use("/api/transpose", transposeRouter);
app.use("/api/user", userRouter);
app.use("/api/posts", postRouter);

// Health check
app.get("/", (req, res) => {
  res.json({ message: "Auth server is running" });
});

// Подключение к MongoDB и запуск сервера
mongoose
  .connect(process.env.MONGODB_URI!)
  .then(() => {
    console.log("Connected to mongoDB");
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
      console.log(`Uploads path: ${uploadsPath}`);
      console.log(`Outputs path: ${outputsPath}`);
      console.log(`Production mode: ${isProduction}`);
    });
  })
  .catch((err) => {
    console.error("MongoDB connection error:", err);
    process.exit(1);
  });

