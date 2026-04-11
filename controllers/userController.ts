import { Request, Response } from "express";
import userService from '../services/userServices';

export const updateProfile = async (req: any, res: Response) => {
  try {
    const userId = req.user._id;
    const { name, email, currentPassword, newPassword, image } = req.body;

    if (newPassword && !currentPassword) {
      return res.status(400).json({ 
        message: "Для смены пароля необходимо указать текущий пароль" 
      });
    }

    const updatedUser = await userService.updateProfile(userId, {
      name,
      email,
      currentPassword,
      newPassword,
      image
    });

    res.json({
      message: "Профиль успешно обновлен",
      user: updatedUser
    });

  } catch (error: any) {
    switch(error.message) {
      case "Пользователь не найден":
        return res.status(404).json({ message: error.message });
      
      case "Email уже используется":
        return res.status(400).json({ message: error.message });
      
      case "Неверный текущий пароль":
        return res.status(401).json({ message: error.message });
      
      default:
        console.error('Ошибка обновления профиля:', error);
        return res.status(500).json({ 
          message: "Ошибка сервера" 
        });
    }
  }
};

export const removeImage = async (req: any, res: Response) => {
  try {
    const userId = req.user._id;
    const user = await userService.removeImage(userId);
    
    res.json({
      message: "Фото профиля удалено",
      user
    });
  } catch (error: any) {
    res.status(500).json({ message: error.message });
  }
};

export const updatePrivacy = async (req: any, res: Response) => {
  try {
    const userId = req.user._id;
    const { isPrivate } = req.body;

    const user = await userService.updatePrivacy(userId, isPrivate);

    res.json({
      message: "Настройки приватности обновлены",
      user
    });
  } catch (error: any) {
    res.status(500).json({ message: error.message });
  }
};

export const getProfile = async (req: any, res: Response) => {
  try {
    const userId = req.params.id;

    const result = await userService.getProfile(userId);

    res.json(result);
  } catch (error: any) {
    if (error.message === "Пользователь не найден") {
      return res.status(404).json({ error: error.message });
    }
    res.status(500).json({ error: "Ошибка загрузки профиля" });
  }
};