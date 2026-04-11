import User from "../models/User";

class UserService {
  async updateProfile(
    userId: string,
    updateData: {
      name?: string;
      email?: string;
      currentPassword?: string;
      newPassword?: string;
      image?: string;
    },
  ) {
    const user = await User.findById(userId);
    if (!user) throw new Error("Пользователь не найден");
    if (updateData.email && updateData.email !== user.email) {
      const existingUser = await User.findOne({ email: updateData.email });
      if (existingUser) throw new Error("Email уже используется");
    }
    if (updateData.newPassword) {
      if (!updateData.currentPassword) {
        throw new Error("Для смены пароля необходимо указать текущий пароль");
      }
      const isPasswordValid = await user.comparePassword(
        updateData.currentPassword,
      );
      if (!isPasswordValid) throw new Error("Неверный текущий пароль");
      user.password = updateData.newPassword; 
    }
    if (updateData.name) user.name = updateData.name;
    if (updateData.email) user.email = updateData.email;
    if (updateData.image) user.image = updateData.image;
    await user.save();
    const updatedUser = await User.findById(user._id).select(
      "-password -refreshToken",
    );
    return updatedUser;
  }
  async removeImage(userId: string) {
    const user = await User.findByIdAndUpdate(userId, { image: null }, { new: true }).select(
      "-password -refreshToken",
    );

    if (!user) throw new Error("Пользователь не найден");
    return user;
  }
  async updatePrivacy(userId: string, isPrivate: boolean) {
    const user = await User.findByIdAndUpdate(
      userId,
      { isPrivate },
      { new: true }
    ).select("-password -refreshToken");

    if (!user) throw new Error("Пользователь не найден");
    return user;
  }

  async getProfile(userId: string) {
  const user = await User.findById(userId).select('name image isPrivate');
  if (!user) throw new Error("Пользователь не найден");

  return {
    user: {
      _id: user._id,
      name: user.name,
      image: user.image,
      isPrivate: user.isPrivate
    },
    isPrivate: user.isPrivate
  };
}

}

export default new UserService();
