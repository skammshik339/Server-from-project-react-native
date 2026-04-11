import mongoose from "mongoose";
import bcrypt from "bcryptjs";
import IUser from "../types/userModelTypes";

const userSchema = new mongoose.Schema<IUser>(
  {
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
    },
    password: {
      type: String,
      required: true,
      minlength: 6,
    },
    name: {
      type: String,
      required: true,
      trim: true,
      maxLength: 25,
    },
    refreshToken: {
      type: String,
      default: null,
    },
    image: {
      type: String,
      default: null
    },
    isEmailVerified: { 
    type: Boolean,
    default: false,
  },
   verifyToken: { 
    type: String,
    default: null,
  },
  isPrivate: {
    type: Boolean,
    default: false
  }, 
  },
  { timestamps: true },
);

userSchema.pre<IUser>("save", async function () {
  if (this.isModified("password")) {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
  }
});

userSchema.methods.comparePassword = async function (
  candidatePassword: string,
) {
  return await bcrypt.compare(candidatePassword, this.password);
};

export default mongoose.model<IUser>("User", userSchema);
