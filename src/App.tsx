import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Examples from './pages/Examples'
import API from './pages/API'
import Architecture from './pages/Architecture'
import { NotFound } from './pages/NotFound'
import DocsIndex from './pages/docs/Index'
import Installation from './pages/docs/Installation'
import Quickstart from './pages/docs/Quickstart'
import Concepts from './pages/docs/Concepts'
import Anchors from './pages/docs/Anchors'
import GoldSets from './pages/docs/GoldSets'
import Metrics from './pages/docs/Metrics'
import Comparison from './pages/docs/Comparison'
import Adapters from './pages/docs/Adapters'
import CLI from './pages/docs/CLI'
import Testing from './pages/docs/Testing'
import Limitations from './pages/docs/Limitations'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/examples" element={<Examples />} />
        <Route path="/api" element={<API />} />
        <Route path="/architecture" element={<Architecture />} />
        
        {/* Documentation Routes */}
        <Route path="/docs" element={<DocsIndex />} />
        <Route path="/docs/installation" element={<Installation />} />
        <Route path="/docs/quickstart" element={<Quickstart />} />
        <Route path="/docs/concepts" element={<Concepts />} />
        <Route path="/docs/anchors" element={<Anchors />} />
        <Route path="/docs/gold-sets" element={<GoldSets />} />
        <Route path="/docs/metrics" element={<Metrics />} />
        <Route path="/docs/comparison" element={<Comparison />} />
        <Route path="/docs/adapters" element={<Adapters />} />
        <Route path="/docs/cli" element={<CLI />} />
        <Route path="/docs/testing" element={<Testing />} />
        <Route path="/docs/limitations" element={<Limitations />} />
        
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  )
}

export default App
