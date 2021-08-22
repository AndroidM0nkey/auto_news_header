import axios from "axios";
import React, { Component } from "react";
import "./App.css";

const URL_REGEXP = /^https?:\/\/(www\.)?interfax.ru/;
const BASE_API_URL = "";

class App extends Component {
	constructor(props) {
		super(props);

		this.state = {
			links: [],
			selectedFile: null,
			data: null
		};

		this.submitFile = this.submitFile.bind(this);
		this.onFileChange = this.onFileChange.bind(this);
		this.addLink = this.addLink.bind(this);
		this.removeLink = this.removeLink.bind(this);
		this.onLinkInputChange = this.onLinkInputChange.bind(this);
	}

	submitFile(e) {
		e.preventDefault();

		if (!this.state.selectedFile) {
			alert("Не выбран файл для загрузки");
			return;
		}

		const formData = new FormData();

		formData.append("File", this.state.selectedFile);

		axios
			.post(`${BASE_API_URL}`, formData)
			.then(({ data }) => this.setState({ data }));
	}

	onFileChange(e) {
		this.setState({ selectedFile: e.target.files[0] });
	}

	addLink() {
		this.setState((state) => {
			let links = Object.assign([], state.links);
			links.push(["", false]);

			return { links };
		});
	}

	removeLink(removeIndex) {
		this.setState((state) => {
			return {
				links: state.links.filter((_, index) => index !== removeIndex)
			};
		});
	}

	onLinkInputChange(e, index) {
		this.setState((state) => {
			state.links[index] = [
				e.target.value,
				URL_REGEXP.test(e.target.value)
			];

			return {
				links: state.links
			};
		});
	}

	render() {
		return (
			<div className="App">
				<div className="file-upload">
					<h3>Загрузите файл с данными</h3>
					<form onSubmit={this.submitFile}>
						<input
							className="file-upload-input"
							type="file"
							name="file"
							accept=".json"
							onChange={this.onFileChange}
						/>
						<button className="file-upload-btn" type="submit">
							Отправить
						</button>
					</form>
				</div>
				<h2>ИЛИ</h2>
				<div className="links-upload">
					<h3>Используйте ссылки на статьи</h3>
					<div>
						{this.state.links.map((value, index) => {
							return (
								<div key={index} className="input-container">
									<input
										onChange={(e) =>
											this.onLinkInputChange(e, index)
										}
										value={value[0]}
										className={value[1] ? "" : "incorrect"}
									/>
									<button
										onClick={() => this.removeLink(index)}
									>
										X
									</button>
								</div>
							);
						})}
					</div>
					<div className="links-buttons">
						<button className="add-link-btn" onClick={this.addLink}>
							+
						</button>
						<button
							className={`submit-links-btn ${
								this.state.links.length > 0 ? "" : "hidden"
							}`}
						>
							Отправить
						</button>
					</div>
				</div>
			</div>
		);
	}
}

export default App;
