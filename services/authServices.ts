import User from "../models/User";
import TokenUtils from "../utils/generateTokens";
import jwt from "jsonwebtoken";
import crypto from "crypto";
import { sendVerificationEmail } from "./emailService";

class AuthService {
  async register(name: string, email: string, password: string) {
    const existingUser = await User.findOne({ email });
    if (existingUser) throw new Error("пользователь уже существует");
    const verifyToken = crypto.randomBytes(32).toString("hex");

    const user = await User.create({
      email,
      password,
      name,
      isEmailVerified: false,
      verifyToken,
    });
    await sendVerificationEmail(email, verifyToken);
    return {
      user: {
        _id: user._id,
        email: user.email,
        name: user.name,
        isEmailVerified: false,
      },
      message: "Проверьте почту для подтверждения",
    };
  }
  async verifyEmail(token: string) {
    const user = await User.findOne({ verifyToken: token });
    if (!user) throw new Error("Недействительная ссылка");
    if (user.isEmailVerified) throw new Error("Email уже подтвержден");

    user.isEmailVerified = true;
    user.verifyToken = null;
    await user.save();

    const tokens = TokenUtils.generateDuoTokens(user._id.toString());
    user.refreshToken = tokens.refreshToken;
    await user.save();

    return {
      user: {
        _id: user._id,
        email: user.email,
        name: user.name,
        isEmailVerified: true,
        image: user.image || null,
      },
      ...tokens,
    };
  }
  async login(email: string, password: string) {
    const user = await User.findOne({ email });
    if (!user) throw new Error("Пользователя с таким email не существует");
    const isPasswordValid = await user.comparePassword(password);
    if (!isPasswordValid) throw new Error("Неправильный пароль");
    if (!user.isEmailVerified) throw new Error("Email не подтвержден");
    const tokens = TokenUtils.generateDuoTokens(user._id.toString());
    user.refreshToken = tokens.refreshToken;
    await user.save();
    return {
      user: { _id: user._id, email: user.email, name: user.name, image: user.image || null},
      ...tokens,
    };
  }
  async logout(userId: string) {
    if (!userId) {
      throw new Error("Пользователя надо обязательно привязать к запросу!!!");
    }
    const user = await User.findByIdAndUpdate(userId, { refreshToken: null });
    if (!user) {
      throw new Error("Пользователь не найден");
    }
    return { message: "Выход из приложения выполнен" };
  }
  async refreshToken(refreshToken: string) {
    if (!refreshToken) throw new Error("Нету refresh токена");

    try {
      const decoded = TokenUtils.verifyAccessRefresh(refreshToken) as {
        userId: string;
      };

      const user = await User.findById(decoded.userId);
      if (!user) throw new Error("Пользователь не найден");

      if (user.refreshToken !== refreshToken) {
        user.refreshToken = null;
        await user.save();
        throw new Error("Подозрительный refresh токен");
      }

      const tokens = TokenUtils.generateDuoTokens(user._id.toString());

      user.refreshToken = tokens.refreshToken;
      await user.save();

      const userNoPassword = await User.findById(user._id).select(
        "-password -refreshToken",
      );

      return {
        user: userNoPassword,
        accessToken: tokens.accessToken,
        refreshToken: tokens.refreshToken,
      };
    } catch (error) {
      if (error instanceof jwt.TokenExpiredError) {
        throw new Error("Refresh токен истёк");
      }
      if (error instanceof jwt.JsonWebTokenError) {
        throw new Error("Недействительный refresh токен");
      }
      throw error;
    }
  }
}

export default new AuthService();
