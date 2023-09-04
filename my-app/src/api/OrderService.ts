import axios from 'axios';

const Orderservice = {
    applyRule: async (regex: string) => {
        const response = await axios.post('http://localhost:5000/apply_rule', {
            regex: regex
        });
        if (response.status !== 200) {
            throw Error(response.statusText);
        }
        return response.data;
    },
}


export default Orderservice;