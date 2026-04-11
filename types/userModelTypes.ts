import mongoose from "mongoose";

export default interface IUser extends mongoose.Document {
  email: string;
  password: string;
  name: string;
  refreshToken: string | null;
  comparePassword(candidatePassword: string): Promise<boolean>;
  image: string;
  isEmailVerified: boolean;
  verifyToken: string | null;
  isPrivate: boolean;
}
