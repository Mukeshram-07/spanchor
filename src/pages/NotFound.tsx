import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { slideUp } from '../utils/animations'

export const NotFound = () => {
  return (
    <motion.div
      variants={slideUp}
      initial="hidden"
      animate="visible"
      className="flex flex-col items-center justify-center min-h-screen gap-lg"
    >
      <h1 className="text-6xl font-bold text-error-500">404</h1>
      <p className="text-2xl text-neutral-600">Page Not Found</p>
      <p className="text-neutral-500 max-w-md text-center">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link
        to="/"
        className="px-lg py-md bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
      >
        Go Home
      </Link>
    </motion.div>
  )
}

export default NotFound
