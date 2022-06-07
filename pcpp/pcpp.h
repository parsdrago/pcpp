namespace pcpp
{

    class Range
    {
    private:
        int m_value;
        const int m_end;
        const int m_step;

    public:
        Range(int begin, int end, int step)
            : m_value(begin), m_end(end), m_step(step)
        {
        }

        int value() const
        {
            return m_value;
        }

        Range begin() const
        {
            return *this;
        }

        int end() const
        {
            return m_end;
        }

        bool operator!=(const int value) const
        {
            return m_step > 0 ? m_value < value : m_value > value;
        }

        void operator++()
        {
            m_value += m_step;
        }
        const int operator*() const
        {
            return m_value;
        }
    };
}
