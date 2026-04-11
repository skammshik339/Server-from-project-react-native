import mongoose from 'mongoose';

const imageSchema = new mongoose.Schema({
    url: String,
    page: Number
})

const transpositionSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    name: String,
    images: [imageSchema],
}, {timestamps: true})

export default mongoose.model('Transposition', transpositionSchema)